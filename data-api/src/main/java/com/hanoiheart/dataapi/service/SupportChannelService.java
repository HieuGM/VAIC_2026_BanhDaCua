package com.hanoiheart.dataapi.service;

import com.hanoiheart.dataapi.dto.SupportChannelDto;
import com.hanoiheart.dataapi.entity.SupportChannel;
import com.hanoiheart.dataapi.repository.SupportChannelRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class SupportChannelService {

    private final SupportChannelRepository repository;

    public SupportChannelService(SupportChannelRepository repository) {
        this.repository = repository;
    }

    public List<SupportChannelDto> list() {
        return repository.findByIsActiveTrueOrderBySortOrderAscIdAsc()
                .stream().map(this::toDto).toList();
    }

    private SupportChannelDto toDto(SupportChannel c) {
        return new SupportChannelDto(c.getId(), c.getChannelType(), c.getLabel(),
                c.getUrl(), c.getPhone(), c.getCampus(), c.getSortOrder());
    }
}
